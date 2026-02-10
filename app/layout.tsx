import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Calculus Reels",
  description: "Learn Calc 1ZB3 through short video reels",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
