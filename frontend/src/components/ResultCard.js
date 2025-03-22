import React from "react";
import { Card, CardContent, Typography, Grid } from "@mui/material";

const ResultCard = ({ result }) => {
  return (
    <Card sx={{ width: 300, margin: "10px", boxShadow: 3 }}>
      <CardContent>
        <Typography variant="h6">{result.name} ({result.symbol})</Typography>
        <Typography variant="body2" color="text.secondary">
          ESG Score: {result.totalEsg}/100
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Environmental Score: {result.environmentScore}/100
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Social Score: {result.socialScore}/100
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Governance Score: {result.governanceScore}/100
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Sector: {result.sector}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Risk Level: {result.overallRisk <= 1.5 ? "Low" : result.overallRisk <= 2.0 ? "Moderate" : "High"}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default ResultCard;
