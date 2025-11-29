import React from "react";
import { createRoot } from "react-dom/client";
import App from "./components/App";
import "./index.css";

if (typeof window !== "undefined") {
  const container = document.getElementById("root");
  const root = createRoot(container);
  root.render(<App />);
} else {
  console.error("window is not defined. This script is meant to run in a browser environment.");
}
