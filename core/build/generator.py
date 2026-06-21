import random
import uuid
from typing import Dict, Any, List

class SpoofingInjector:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)

    def inject_spoofing(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Injects a spoofing pattern into an existing clean scenario.
        """
        events = list(scenario["events"])
        if not events:
            raise ValueError("Cannot inject spoofing into a scenario with no events.")

        # Determine baseline for price from the last event
        base_price = events[-1]["price"]
        side = self.rng.choice(["bid", "ask"])
        trader_id = f"trader_spoof_{self.rng.randint(100, 999)}"
        order_id = f"ord_spoof_{self.rng.getrandbits(48):012x}"
        
        # Determine injection time: somewhere in the middle of the scenario
        start_ts = events[0]["ts"]
        end_ts = events[-1]["ts"]
        place_ts = self.rng.randint(start_ts, max(start_ts, end_ts - 100))
        cancel_ts = place_ts + self.rng.randint(50, 500)

        # Price logic: Spoof bids are well below mid, Spoof asks are well above
        offset = base_price * self.rng.uniform(0.05, 0.15)
        price = round(base_price - offset if side == "bid" else base_price + offset, 4)
        size = round(self.rng.uniform(50.0, 100.0), 2) # Large size

        place_evt_id = f"evt_inj_{self.rng.getrandbits(48):012x}"
        cancel_evt_id = f"evt_inj_{self.rng.getrandbits(48):012x}"

        place_event = {
            "event_id": place_evt_id,
            "ts": place_ts,
            "type": "place",
            "order_id": order_id,
            "side": side,
            "price": float(price),
            "size": float(size),
            "owner_id": trader_id
        }

        cancel_event = {
            "event_id": cancel_evt_id,
            "ts": cancel_ts,
            "type": "cancel",
            "order_id": order_id,
            "side": side,
            "price": float(price),
            "size": float(size),
            "owner_id": trader_id
        }

        events.extend([place_event, cancel_event])
        events.sort(key=lambda x: x["ts"])

        # Update Ground Truth
        explanation = (
            f"Trader {trader_id} placed a large {side} order at {price} "
            f"({offset/base_price:.1%} away from market) and cancelled it "
            f"{cancel_ts - place_ts}ms later to create false pressure."
        )

        new_scenario = scenario.copy()
        new_scenario["events"] = events
        new_scenario["duration_ms"] = max(e["ts"] for e in events)
        new_scenario["ground_truth"] = {
            "label": "manipulated",
            "manipulation_type": "spoofing",
            "implicated_event_ids": [place_evt_id, cancel_evt_id],
            "explanation": explanation
        }

        return new_scenario

class ScenarioSetGenerator:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)

    def generate_set(self, count: int, fraction: float, market: str, events_per_scenario: int) -> List[Dict[str, Any]]:
        if not 0 <= fraction <= 1:
            raise ValueError(f"Fraction must be between 0 and 1, got {fraction}")
        
        scenarios = []
        # Generate specific seeds for each scenario to ensure independence and determinism
        seeds = [self.rng.getrandbits(32) for _ in range(count)]
        
        # Determine which indices will be manipulated
        num_manipulated = int(round(count * fraction))
        indices = list(range(count))
        self.rng.shuffle(indices)
        manipulated_indices = set(indices[:num_manipulated])

        for i in range(count):
            local_seed = seeds[i]
            gen = ScenarioGenerator(local_seed)
            scenario = gen.generate_clean_scenario(market, events_per_scenario)
            
            if i in manipulated_indices:
                injector = SpoofingInjector(local_seed + 1) # Offset seed for injection
                scenario = injector.inject_spoofing(scenario)
            
            scenarios.append(scenario)
        
        return scenarios

class ScenarioGenerator:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.current_ts = 0
        self.mid_price = 100.0
        self.order_ids = []

    def generate_clean_scenario(self, market: str, target_events: int) -> Dict[str, Any]:
        """
        Generates a clean scenario with stochastic order flow.
        """
        scenario_id = f"scn_{self.rng.getrandbits(48):012x}"
        events = []
        
        for i in range(target_events):
            event = self._generate_event()
            events.append(event)
            
        # Ground truth for a clean scenario
        ground_truth = {
            "label": "clean",
            "manipulation_type": None,
            "implicated_event_ids": [],
            "explanation": "Stochastically generated baseline order flow with no injected manipulations."
        }
        
        return {
            "scenario_id": scenario_id,
            "market": market,
            "duration_ms": self.current_ts,
            "events": events,
            "ground_truth": ground_truth
        }

    def _generate_event(self) -> Dict[str, Any]:
        # Increment time (1ms to 500ms)
        self.current_ts += self.rng.randint(1, 500)
        
        # Drift mid price
        self.mid_price += self.rng.uniform(-0.5, 0.5)
        self.mid_price = max(0.01, self.mid_price)
        
        event_id = f"evt_{self.rng.getrandbits(48):012x}"
        side = self.rng.choice(["bid", "ask"])
        
        # Price logic: Bids below mid, Asks above mid
        if side == "bid":
            price = round(self.mid_price - self.rng.uniform(0.01, 2.0), 4)
        else:
            price = round(self.mid_price + self.rng.uniform(0.01, 2.0), 4)
        
        price = max(0.0001, price)
        size = round(self.rng.uniform(0.1, 10.0), 2)
        owner_id = f"trader_{self.rng.randint(1, 10)}"
        
        # Determine event type
        # In a clean scenario, we mostly place. 
        # For simplicity in M1 generation, we focus on placement to satisfy requirements.
        event_type = "place"
        order_id = f"ord_{self.rng.getrandbits(48):012x}"
        
        return {
            "event_id": event_id,
            "ts": self.current_ts,
            "type": event_type,
            "order_id": order_id,
            "side": side,
            "price": float(price),
            "size": float(size),
            "owner_id": owner_id
        }