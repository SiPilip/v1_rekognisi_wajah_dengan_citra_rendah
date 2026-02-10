import {
  ResponsiveContainer,
  ScatterChart,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  Scatter,
  LabelList,
} from "recharts";
import { Box, Typography } from "@mui/material";
import React from "react";

interface ConfusionMatrixPlotProps {
  matrix: number[][];
  labels: string[];
  title: string;
}

// Helper untuk mendapatkan warna berdasarkan nilai sel
const getColor = (value: number, max: number) => {
  if (max === 0) return "#eeeeee"; // Abu-abu jika tidak ada data
  const intensity = Math.floor((value / max) * 200);
  return `rgb(${255 - intensity}, ${255 - intensity / 2}, 255)`; // Skala warna kebiruan
};

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <Box
        sx={{
          bgcolor: "background.paper",
          p: 1,
          border: 1,
          borderColor: "divider",
        }}
      >
        <Typography variant="body2">{`True: ${data.yLabel}`}</Typography>
        <Typography variant="body2">{`Predicted: ${data.xLabel}`}</Typography>
        <Typography variant="body2" fontWeight="bold">
          {`Count: ${data.value}`}
        </Typography>
      </Box>
    );
  }
  return null;
};

const ConfusionMatrixPlot = ({
  matrix,
  labels,
  title,
}: ConfusionMatrixPlotProps) => {
  // Transformasi data matriks menjadi format yang bisa dibaca Recharts
  const data = matrix.flatMap((row, i) =>
    row.map((value, j) => ({
      x: j, // Predicted
      y: i, // True
      value: value,
      xLabel: labels[j],
      yLabel: labels[i],
    }))
  );

  const maxValue = Math.max(...data.map((d) => d.value));

  return (
    <Box sx={{ width: "100%", height: 400 }}>
      <Typography variant="h6" align="center">
        {title}
      </Typography>
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 60 }}>
          <XAxis
            type="number"
            dataKey="x"
            name="Predicted"
            interval={0}
            ticks={labels.map((_, index) => index)}
            tick={{ angle: -45, textAnchor: "end" }}
            label={{
              value: "Predicted Label",
              position: "insideBottom",
              offset: -40,
            }}
            tickFormatter={(tick) => labels[tick]}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="True"
            interval={0}
            reversed={true}
            ticks={labels.map((_, index) => index)}
            label={{
              value: "True Label",
              angle: -90,
              position: "insideLeft",
              offset: -40,
            }}
            tickFormatter={(tick) => labels[tick]}
          />
          <ZAxis dataKey="value" range={[0, 1000]} />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            content={<CustomTooltip />}
          />
          <Scatter
            data={data}
            shape={({ cx, cy, ...props }) => {
              const { payload } = props;
              const size = 50; // Ukuran sel
              return (
                <rect
                  x={cx - size / 2}
                  y={cy - size / 2}
                  width={size}
                  height={size}
                  fill={getColor(payload.value, maxValue)}
                  stroke="#fff"
                />
              );
            }}
          >
            <LabelList
              dataKey="value"
              position="center"
              fill="#000"
              fontSize={12}
            />
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ConfusionMatrixPlot;
