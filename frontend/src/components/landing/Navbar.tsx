"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const NAV_LINKS = [
  { id: "masalah", label: "Masalah" },
  { id: "metodologi", label: "Metodologi" },
  { id: "hasil", label: "Hasil" },
  { id: "interpretasi", label: "Interpretasi" },
  { id: "cara-kerja", label: "Cara Kerja" },
  { id: "peneliti", label: "Peneliti" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("");

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActiveSection(e.target.id);
        });
      },
      { threshold: 0.3 }
    );
    NAV_LINKS.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    setMobileOpen(false);
  };

  return (
    <>
      <motion.nav
        initial={{ y: -80 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.4 }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? "bg-white/90 backdrop-blur-md shadow-sm border-b border-border"
            : "bg-transparent"
        }`}
      >
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand flex items-center justify-center text-white text-sm font-bold shrink-0">
              SD
            </div>
            <span
              className={`font-semibold text-sm sm:text-base transition-colors ${
                scrolled ? "text-text" : "text-white"
              }`}
            >
              StuntingDetect
            </span>
          </div>

          <div className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map(({ id, label }) => (
              <button
                key={id}
                onClick={() => scrollTo(id)}
                className={`px-3 py-2 text-sm rounded-lg transition-all duration-200 ${
                  activeSection === id
                    ? scrolled
                      ? "text-brand font-medium"
                      : "text-white font-medium underline decoration-2 underline-offset-4"
                    : scrolled
                      ? "text-text-secondary hover:text-text"
                      : "text-white/80 hover:text-white"
                }`}
              >
                {label}
              </button>
            ))}
            <a
              href="/dashboard"
              className="ml-3 px-5 py-2 rounded-lg bg-brand text-white text-sm font-medium hover:bg-brand-dark active:scale-[0.97] transition-all"
            >
              Dashboard
            </a>
          </div>

          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 rounded-lg active:scale-90 transition-transform"
            aria-label="Menu"
          >
            <svg
              className={`w-6 h-6 transition-colors ${scrolled ? "text-text" : "text-white"}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              {mobileOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </motion.nav>

      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="fixed top-0 right-0 bottom-0 w-72 bg-white z-50 shadow-xl pt-24 px-6"
            >
              <div className="flex flex-col gap-2">
                {NAV_LINKS.map(({ id, label }) => (
                  <button
                    key={id}
                    onClick={() => scrollTo(id)}
                    className="text-left px-4 py-3 rounded-lg text-text-secondary hover:bg-surface-alt hover:text-text transition-colors text-sm"
                  >
                    {label}
                  </button>
                ))}
                <hr className="my-2 border-border" />
                <a
                  href="/dashboard"
                  className="text-center px-4 py-3 rounded-lg bg-brand text-white font-medium text-sm"
                >
                  Dashboard
                </a>
              </div>
            </motion.div>
            <div
              className="fixed inset-0 bg-black/30 z-40 md:hidden"
              onClick={() => setMobileOpen(false)}
            />
          </>
        )}
      </AnimatePresence>
    </>
  );
}