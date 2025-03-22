import React from "react";
import { TextField, Box } from "@mui/material";

const TextInput = ({ query, setQuery }) => {
  return (
    <Box sx={{ width: "100%", display: "flex", justifyContent: "center", margin: "20px" }}>
      <TextField
        label="Enter search query"
        variant="outlined"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        sx={{ width: "60%" }}
      />
    </Box>
  );
};

export default TextInput;
