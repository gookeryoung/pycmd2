import "./index.css";

import { RootApp } from "./RootApp";
import { enableMapSet } from "immer";
import React, { Suspense } from "react";
import ReactDOM from "react-dom/client";

enableMapSet();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Suspense fallback="...loading">
      <RootApp />
    </Suspense>
  </React.StrictMode >,
);
