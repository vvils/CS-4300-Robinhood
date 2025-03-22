import React from "react";
import { Slider, Typography, Box } from "@mui/material";

const SliderInput = ({ value, setValue }) => {
  return (
    <Box sx={{ width: 300, margin: "20px auto" }}>
      <Typography gutterBottom>Risk Tolerance: {value}</Typography>
      <Slider
        value={value}
        onChange={(e, newValue) => setValue(newValue)}
        min={1}
        max={100}
        step={1}
        marks
      />
    </Box>
  );
};

export default SliderInput;
