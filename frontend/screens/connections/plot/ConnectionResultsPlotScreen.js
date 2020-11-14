import * as React from "react";
import ConnectionResultsPlot from "./ConnectionResultsPlot";

export default function ConnectionResultsPlotScreen({ navigation, route }) {
  const startDateTime = new Date(route.params.startDateTime);
  const connections = route.params.connections;

  return (
    <ConnectionResultsPlot
      connections={connections}
      startDateTime={startDateTime}
      navigation={navigation}
    />
  );
}
