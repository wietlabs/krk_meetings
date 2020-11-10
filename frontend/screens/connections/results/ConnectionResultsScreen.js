import * as React from "react";
import ConnectionResults from "./ConnectionResults";
import connections_json from "./connections.json"; // TODO: use axios

export default function ConnectionResultsScreen({ navigation }) {
  const connections = connections_json.connections.slice(0, 25); // TODO: get connections from route.params

  return (
    <ConnectionResults connections={connections} navigation={navigation} />
  );
}
