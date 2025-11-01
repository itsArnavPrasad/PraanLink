import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import CheckIn from "./pages/CheckIn";
import Upload from "./pages/Upload";
import Summaries from "./pages/Summaries";
import Appointments from "./pages/Appointments";
import AgentCall from "./pages/AgentCall";
import Insurance from "./pages/Insurance";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<CheckIn />} />
            <Route path="upload" element={<Upload />} />
            <Route path="summaries" element={<Summaries />} />
            <Route path="appointments" element={<Appointments />} />
            <Route path="insurance" element={<Insurance />} />
          </Route>
          <Route path="agent-call" element={<AgentCall />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
