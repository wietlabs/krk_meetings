import * as React from "react";
import { IconButton } from "react-native-paper";
import ConnectionResults from "./ConnectionResults";

export default function ConnectionResultsScreen({ navigation, route }) {
  const connections = route.params.connections;

  const handleShowPlot = () => {
    navigation.navigate("ConnectionResultsPlot", { connections });
  };

  React.useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <IconButton
          icon="chart-bar"
          onPress={handleShowPlot}
          style={{ marginRight: 16 }}
        />
      ),
    });
  }, [navigation]);

  return (
    <ConnectionResults connections={connections} navigation={navigation} />
  );
}
