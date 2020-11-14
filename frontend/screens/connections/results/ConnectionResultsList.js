import * as React from "react";
import { FlatList } from "react-native";
import ConnectionResultItem from "./ConnectionResultItem";

export default function ConnectionResultsList({ connections, navigation }) {
  const renderItem = ({ item: connection }) => {
    const handlePress = () => {
      navigation.navigate("ConnectionDetails", { connection });
    };

    return (
      <ConnectionResultItem connection={connection} onPress={handlePress} />
    );
  };

  return (
    <FlatList
      data={connections}
      renderItem={renderItem}
      keyExtractor={(item, index) => index.toString()}
      contentContainerStyle={{ padding: 16, paddingBottom: 8 }}
    />
  );
}
