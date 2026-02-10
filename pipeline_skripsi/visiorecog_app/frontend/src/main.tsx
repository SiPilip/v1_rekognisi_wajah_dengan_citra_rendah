import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

// Konfigurasi tema gelap untuk Material UI
const darkTheme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2", // Anda bisa menyesuaikan warna ini
    },
    background: {
      default: "#fefefe",
      paper: "#ffffffec",
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
