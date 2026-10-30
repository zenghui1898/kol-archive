import { Link, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Cast } from "./pages/Cast";
import { GuaDetail } from "./pages/GuaDetail";
import { HistoryPage } from "./pages/HistoryPage";
import { Home } from "./pages/Home";
import { IndexPage } from "./pages/IndexPage";
import { Result } from "./pages/Result";

export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/cast" element={<Cast />} />
        <Route path="/result/:id" element={<Result />} />
        <Route path="/gua" element={<IndexPage />} />
        <Route path="/gua/:id" element={<GuaDetail />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route
          path="*"
          element={
            <div className="empty-state">
              <h1>这条路没有卦</h1>
              <Link className="btn" to="/">
                回到摇卦
              </Link>
            </div>
          }
        />
      </Route>
    </Routes>
  );
}
