import * as React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import FindConnectionsScreen from "../screens/connections/find/FindConnectionsScreen";
import ConnectionResultsScreen from "../screens/connections/results/ConnectionResultsScreen";
import ConnectionResultsPlotScreen from "../screens/connections/plot/ConnectionResultsPlotScreen";
import ConnectionDetailsScreen from "../screens/connections/details/ConnectionDetailsScreen";

const Stack = createStackNavigator();

export default function ConnectionsStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="FindConnections"
        component={FindConnectionsScreen}
        options={{ title: "Wyszukiwarka połączeń" }}
      />
      <Stack.Screen
        name="ConnectionResults"
        component={ConnectionResultsScreen}
        options={{ title: "Wyniki wyszukiwania" }}
      />
      <Stack.Screen
        name="ConnectionResultsPlot"
        component={ConnectionResultsPlotScreen}
        options={{ title: "Wyniki wyszukiwania" }}
      />
      <Stack.Screen
        name="ConnectionDetails"
        component={ConnectionDetailsScreen}
        options={{ title: "Szczegóły połączenia" }}
      />
    </Stack.Navigator>
  );
}
