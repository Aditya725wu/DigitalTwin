import type { Metadata } from "next";
import { ToastProvider } from "@/components/ToastProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "CardioTwin - Cardiac Digital Twin Dashboard",
  description: "AI-powered cardiovascular disease prediction and monitoring platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        {children}
        <ToastProvider />
      </body>
    </html>
  );
}
