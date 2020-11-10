import * as React from "react";
import { Text, List } from "react-native-paper";
import { datetimeToHour } from "../../../../utils";

export default function TransferAction({ transfer }) {
  const start_time = datetimeToHour(transfer.start_datetime);
  const end_time = datetimeToHour(transfer.end_datetime);

  const start_stop_name = transfer.start_stop_name;
  const end_stop_name = transfer.end_stop_name;

  const title = (
    <Text>
      {transfer.route_name}&nbsp;&rarr;&nbsp;{transfer.headsign}
    </Text>
  );
  const description =
    start_time + " " + start_stop_name + "\n" + end_time + " " + end_stop_name;

  const icon = transfer.route_name.length == 3 ? "bus" : "tram";

  return (
    <List.Item
      title={title}
      description={description}
      left={(props) => (
        <List.Icon {...props} icon={icon} style={{ margin: 0 }} />
      )}
      style={{ paddingLeft: 0, paddingRight: 0 }}
    />
  );
}
