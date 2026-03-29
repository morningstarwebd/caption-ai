import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Caption AI — Video Caption Editor",
  description: "Open-source AI-powered video captioning with Premiere Pro-inspired editor",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
