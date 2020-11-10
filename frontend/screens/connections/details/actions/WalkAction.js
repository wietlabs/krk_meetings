import * as React from "react";
import { List } from "react-native-paper";

export default function WalkAction({ walking }) {
  const start_stop_name = walking.start_stop_name;
  const end_stop_name = walking.end_stop_name;

  const title = walking.duration_in_minutes + " min";
  const description = start_stop_name + "\n" + end_stop_name;

  return (
    <List.Item
      title={title}
      description={description}
      left={(props) => (
        <List.Icon {...props} icon="walk" style={{ margin: 0 }} />
      )}
      style={{ paddingLeft: 0, paddingRight: 0 }}
    />
  );
}
