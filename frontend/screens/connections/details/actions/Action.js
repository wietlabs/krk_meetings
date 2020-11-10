import * as React from "react";
import TransferAction from "./TransferAction";
import WalkAction from "./WalkAction";

export default function Action({ action }) {
  const type = action.type;

  switch (type) {
    case "transfer":
      return <TransferAction transfer={action} />;

    case "walking":
      return <WalkAction walking={action} />;
  }
}
