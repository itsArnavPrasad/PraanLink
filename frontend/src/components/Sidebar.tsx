import { NavLink } from "react-router-dom";
import { 
  MessageSquare, 
  Upload, 
  FileText, 
  Calendar, 
  Shield,
  Activity
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Check-In", href: "/", icon: MessageSquare },
  { name: "Upload Reports", href: "/upload", icon: Upload },
  { name: "Summaries", href: "/summaries", icon: FileText },
  { name: "Appointments", href: "/appointments", icon: Calendar },
  { name: "Insurance", href: "/insurance", icon: Shield },
];

export const Sidebar = () => {
  return (
    <div className="flex h-screen w-64 flex-col border-r border-border bg-card">
      {/* Logo/Brand */}
      <div className="flex h-16 items-center gap-3 border-b border-border px-6">
        <Activity className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-xl font-bold text-foreground">PraanLink</h1>
          <p className="text-xs text-muted-foreground">Health Companion</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            end={item.href === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-smooth",
                isActive
                  ? "bg-primary-lighter text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )
            }
          >
            <item.icon className="h-5 w-5" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-border p-4">
        <div className="rounded-lg bg-primary-lighter p-3">
          <p className="text-xs font-medium text-primary">Proactive Healthcare</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Your health, monitored continuously
          </p>
        </div>
      </div>
    </div>
  );
};
