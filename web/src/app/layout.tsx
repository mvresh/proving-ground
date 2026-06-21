import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ProvingGround — manipulation eval harness",
  description:
    "Manufacture labelled order-book reality, run detectors, score catch rate, and write a tamper-evident record to Walrus.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}
