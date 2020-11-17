import * as React from "react";
import { IconButton } from "react-native-paper";
import ConnectionResultsList from "./ConnectionResultsList";

export default function ConnectionResultsScreen({ navigation, route }) {
  const startDateTime = route.params.startDateTime;
  const connections = route.params.connections;

  const handleShowPlot = () => {
    navigation.navigate("ConnectionResultsPlot", {
      startDateTime,
      connections,
    });
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
    <ConnectionResultsList connections={connections} navigation={navigation} />
  );
}
