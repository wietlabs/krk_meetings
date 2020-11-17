import * as React from "react";
import { Card, Text } from "react-native-paper";
import RouteButton from "./RouteChip";
import WalkButton from "./WalkChip";
import { datetimeToHour, filterTransfers } from "../../../utils";

export default function ConnectionResultItem({ connection, onPress }) {
  const actions = connection.actions;

  const transfers = filterTransfers(actions);

  const first_transfer = transfers[0];
  const last_transfer = transfers[transfers.length - 1];

  const start_datetime = datetimeToHour(first_transfer.start_datetime);
  const end_datetime = datetimeToHour(last_transfer.end_datetime);

  const start_stop_name = first_transfer.start_stop_name;
  const end_stop_name = last_transfer.end_stop_name;

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
        {transfers.map((action, i) => {
          switch (action.type) {
            case "transfer":
              return (
                <RouteButton routeName={action.route_name} key={i} nth={i} />
              );
            case "walking":
              return <WalkButton key={i} />;
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
