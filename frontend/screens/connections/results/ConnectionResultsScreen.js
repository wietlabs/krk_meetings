import * as React from "react";
import ConnectionResults from "./ConnectionResults";

export default function ConnectionResultsScreen({ navigation, route }) {
  const connections = route.params.connections;

  return (
    <ConnectionResults connections={connections} navigation={navigation} />
  );
}
