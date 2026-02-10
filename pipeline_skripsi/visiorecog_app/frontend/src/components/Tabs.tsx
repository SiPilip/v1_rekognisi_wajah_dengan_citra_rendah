import { KeyboardEvent } from "react";
import TabsBase from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Box from "@mui/material/Box";

export interface TabItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
}

interface TabsProps {
  tabs: TabItem[];
  value: string;
  onChange: (key: string) => void;
  className?: string;
}

export default function Tabs({ tabs, value, onChange, className }: TabsProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    const currentIndex = tabs.findIndex((t) => t.key === value);
    if (currentIndex === -1) return;
    if (e.key === "Home") {
      e.preventDefault();
      onChange(tabs[0].key);
    } else if (e.key === "End") {
      e.preventDefault();
      onChange(tabs[tabs.length - 1].key);
    }
  };

  const muiValue = tabs.findIndex((t) => t.key === value);

  return (
    <Box className={className} sx={{ width: "100%" }} onKeyDown={handleKeyDown}>
      <TabsBase
        value={muiValue < 0 ? 0 : muiValue}
        onChange={(_, idx: number) => onChange(tabs[idx].key)}
        variant="scrollable"
        scrollButtons="auto"
        aria-label="tabs"
        textColor="inherit"
        indicatorColor="primary"
        sx={{
          borderRadius: 1,
          minHeight: 40,
          px: 1,
          bgcolor: "background.paper",
        }}
      >
        {tabs.map((tab) => (
          <Tab
            key={tab.key}
            label={tab.label}
            icon={tab.icon}
            iconPosition={tab.icon ? "start" : undefined}
            sx={{ minHeight: 40, textTransform: "none", fontWeight: 600 }}
          />
        ))}
      </TabsBase>
    </Box>
  );
}
