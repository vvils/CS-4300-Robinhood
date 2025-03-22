import React, { useState } from "react";
import { Container, Box, Button, Grid, Typography } from "@mui/material";
import SliderInput from "./components/SliderInput";
import TextInput from "./components/TextInput";
import ResultCard from "./components/ResultCard";

const App = () => {
  const [value, setValue] = useState(50);
  const [query, setQuery] = useState("");
  
  // Hardcoded result data for demonstration, matching the format you described
  const results = [
    {
      symbol: "TSLA",
      name: "Tesla",
      score: 92,
      sector: "Technology",
      environmentScore: 92,
      socialScore: 80,
      governanceScore: 85,
      totalEsg: 90,
      overallRisk: 1.8
    },
    {
      symbol: "NEE",
      name: "NextEra Energy",
      score: 89,
      sector: "Energy",
      environmentScore: 89,
      socialScore: 75,
      governanceScore: 80,
      totalEsg: 88,
      overallRisk: 1.2
    },
    {
      symbol: "XOM",
      name: "ExxonMobil",
      score: 42,
      sector: "Energy",
      environmentScore: 42,
      socialScore: 50,
      governanceScore: 55,
      totalEsg: 45,
      overallRisk: 1.5
    }
  ];

  return (
    <Container>
      <Typography variant="h4" sx={{ textAlign: "center", margin: "20px 0" }}>
        RobinGood
      </Typography>
      
      <TextInput query={query} setQuery={setQuery} />
      <SliderInput value={value} setValue={setValue} />

      <Box sx={{ textAlign: "center", margin: "20px 0" }}>
        <Button variant="contained" onClick={() => console.log("Search clicked")}>
          Search
        </Button>
      </Box>

      <Grid container spacing={2} justifyContent="center">
        {results.map((result, index) => (
          <Grid item key={index}>
            <ResultCard result={result} />
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default App;
