import * as React from "react";
import { Card, Text } from "react-native-paper";
import RouteButton from "./RouteChip";
import WalkButton from "./WalkChip";
import { datetimeToHour, filterTransfers } from "../../../utils";

export default function ConnectionResultItem({ connection, onPress }) {
  const actions = connection.actions;

  const transfers = filterTransfers(actions);

  let start_datetime, end_datetime, start_stop_name, end_stop_name;
  if (transfers.length > 0) {
    const first_transfer = transfers[0];
    const last_transfer = transfers[transfers.length - 1];
    start_datetime = datetimeToHour(first_transfer.start_datetime);
    end_datetime = datetimeToHour(last_transfer.end_datetime);
    start_stop_name = first_transfer.start_stop_name;
    end_stop_name = last_transfer.end_stop_name;
  } else {
    const action = actions[0];
    const now = new Date();
    start_datetime = now.toLocaleTimeString().slice(0, 5);
    end_datetime = new Date(
      now.getTime() + action.duration_in_minutes * 60 * 1000
    )
      .toLocaleTimeString()
      .slice(0, 5);
    start_stop_name = action.start_stop_name;
    end_stop_name = action.end_stop_name;
  }

  return (
    <Card onPress={onPress} style={{ marginTop: 12, marginBottom: 16 }}>
      <Card.Content
        style={{
          flex: 1,
          flexDirection: "row",
          marginTop: -30,
          marginBottom: 6,
        }}
      >
        {actions.map((action, i) => {
          switch (action.type) {
            case "transfer":
              return (
                <RouteButton routeName={action.route_name} key={i} nth={i} />
              );
            case "walking":
              return (
                <WalkButton duration={action.duration_in_minutes} key={i} />
              );
          }
        })}
      </Card.Content>
      <Card.Content>
        <Text>
          <Text style={{ fontWeight: "bold" }}>{start_datetime}</Text>
          &nbsp;{start_stop_name}
        </Text>
        <Text>
          <Text style={{ fontWeight: "bold" }}>{end_datetime}</Text>&nbsp;
          {end_stop_name}
        </Text>
      </Card.Content>
    </Card>
  );
}
