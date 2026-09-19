import type { Metadata } from "next";
import { DM_Sans, Space_Grotesk } from "next/font/google";
import { AppShell } from "@/components/layout/app-shell";
import { AgriOSProvider } from "@/components/providers/agri-os-provider";
import "./globals.css";

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
});

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AgriOS | KRISHI-X",
  description: "Agricultural operations mission control demo",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${dmSans.variable} ${spaceGrotesk.variable}`}>
      <body>
        <AgriOSProvider>
          <AppShell>{children}</AppShell>
        </AgriOSProvider>
      </body>
    </html>
  );
}
