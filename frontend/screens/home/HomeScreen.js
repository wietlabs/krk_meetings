import * as React from "react";
import { View } from "react-native";
import { Button, Searchbar } from "react-native-paper";

export default function HomeScreen({ navigation }) {
  const [startStopName, setStartStopName] = React.useState("");
  const [endStopName, setEndStopName] = React.useState("");

  const handleSwap = () => {
    setStartStopName(endStopName);
    setEndStopName(startStopName);
  };

  const handleSubmit = () => {
    navigation.navigate("ConnectionResults");
  };

  return (
    <View style={{ alignItems: "center", padding: 20, paddingTop: 80 }}>
      <Searchbar
        placeholder="Przystanek początkowy"
        value={startStopName}
        icon="adjust"
        style={{ marginBottom: 16 }}
        onChangeText={(text) => setStartStopName(text)}
      />
      <Button
        mode="outlined"
        compact={true}
        icon="autorenew"
        style={{ marginBottom: 16 }}
        color="gray"
        onPress={handleSwap}
      ></Button>
      <Searchbar
        placeholder="Przystanek końcowy"
        value={endStopName}
        icon="map-marker"
        style={{ marginBottom: 80 }}
        onChangeText={(text) => setEndStopName(text)}
      />
      <Button mode="contained" onPress={handleSubmit}>
        Wyszukaj połączenie
      </Button>
    </View>
  );
}
