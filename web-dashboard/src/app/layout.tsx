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
        <div className="bg-slate-900 px-4 py-2 text-center text-xs font-medium text-slate-100">Synthetic demo data. Not a medical device. Not for clinical decisions.</div>
        {children}
        <ToastProvider />
      </body>
    </html>
  );
}
