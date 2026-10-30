import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { loadTheme, saveTheme, type ThemeName } from "../lib/storage";

export function Layout() {
  const [theme, setTheme] = useState<ThemeName>(() => loadTheme());
  const location = useLocation();

  useEffect(() => {
    saveTheme(theme);
  }, [theme]);

  return (
    <div className="shell">
      <header className="top">
        <NavLink to="/" className="brand" end>
          摇卦
        </NavLink>
        <nav>
          <NavLink to="/cast">起卦</NavLink>
          <NavLink to="/gua">六十四卦</NavLink>
          <NavLink to="/history">记录</NavLink>
        </nav>
        <button
          type="button"
          className="theme"
          aria-pressed={theme === "night"}
          onClick={() => setTheme((current) => (current === "day" ? "night" : "day"))}
        >
          {theme === "night" ? "昼" : "夜"}
        </button>
      </header>
      <main key={location.pathname} className="page">
        <Outlet />
      </main>
      <footer className="foot">
        <p>摇卦 · 铜钱只在这台浏览器里摇动 · 供自省，不替你决定</p>
      </footer>
    </div>
  );
}
