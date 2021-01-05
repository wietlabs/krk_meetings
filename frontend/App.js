import * as React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createMaterialBottomTabNavigator } from "@react-navigation/material-bottom-tabs";
import { DefaultTheme, Provider as PaperProvider } from "react-native-paper";
import { registerLinkingHandler } from "./LinkManager";
import MeetingsStack from "./stacks/MeetingsStack";
import ConnectionsStack from "./stacks/ConnectionsStack";
import SequenceStack from "./stacks/SequenceStack";
import TimetableStack from "./stacks/TimetableStack";

const Tab = createMaterialBottomTabNavigator();

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: "#0088ff",
  },
};

export const navigationRef = React.createRef();

export default function App() {
  React.useEffect(() => {
    registerLinkingHandler(navigationRef);
  }, []);

  return (
    <PaperProvider theme={theme}>
      <NavigationContainer ref={navigationRef}>
        <Tab.Navigator
          initialRouteName="ConnectionsStack"
          inactiveColor="#bbb"
          barStyle={{ backgroundColor: "whitesmoke" }}
          lazy={false}
        >
          <Tab.Screen
            name="MeetingsStack"
            component={MeetingsStack}
            options={{
              tabBarLabel: "Spotkania",
              tabBarIcon: "account-multiple",
            }}
          />
          <Tab.Screen
            name="ConnectionsStack"
            component={ConnectionsStack}
            options={{
              tabBarLabel: "Połączenia",
              tabBarIcon: "map-search-outline",
            }}
          />
          <Tab.Screen
            name="SequenceStack"
            component={SequenceStack}
            options={{
              tabBarLabel: "Sekwencja",
              tabBarIcon: "format-list-numbered",
            }}
          />
          {/* <Tab.Screen
            name="TimetableStack"
            component={TimetableStack}
            options={{
              tabBarLabel: "Rozkłady jazdy",
              tabBarIcon: "bus-clock",
            }}
          /> */}
        </Tab.Navigator>
      </NavigationContainer>
    </PaperProvider>
  );
}
