import React, { useState } from "react";
import { Container, Box, Button, Grid, Typography } from "@mui/material";
import SliderInput from "./components/SliderInput";
import TextInput from "./components/TextInput";
import ResultCard from "./components/ResultCard";

const App = () => {
  const [value, setValue] = useState(50);  
  const [query, setQuery] = useState("");  
  const [results, setResults] = useState([]); 

  const fetchResults = async () => {
    if (query.trim() === "") return;

    console.log("Fetching results for query:", query);

    try {
      const response = await fetch(`http://localhost:5000/query?query=${query}`);
      console.log("Response received:", response);

      if (!response.ok) {
        console.error("Error with the API response:", response.statusText);
        return;
      }

      const data = await response.json();
      console.log("Data from backend:", data);

      if (Array.isArray(data)) {
        setResults(data);  
      } else {
        console.error("Unexpected response format:", data);
      }
    } catch (error) {
      console.error("Error during fetch:", error);
    }
  };

  return (
    <Container>
      <Typography variant="h4" sx={{ textAlign: "center", margin: "20px 0" }}>
        RobinGood
      </Typography>
      
      <TextInput query={query} setQuery={setQuery} />
      <SliderInput value={value} setValue={setValue} />

      <Box sx={{ textAlign: "center", margin: "20px 0" }}>
        <Button variant="contained" onClick={fetchResults}>
          Search
        </Button>
      </Box>

      <Grid container spacing={2} justifyContent="center">
        <Typography variant="h6">Results count: {results.length}</Typography>
        {results.length > 0 ? (
          results.map((result, index) => (
            <Grid item key={index}>
              <ResultCard result={result} />
            </Grid>
          ))
        ) : (
          <Typography>No results found.</Typography>
        )}
      </Grid>
    </Container>
  );
};

export default App;

