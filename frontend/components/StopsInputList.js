import * as React from "react";
import { ScrollView } from "react-native";
import { TextInput, Button } from "react-native-paper";

export default function StopsInputList({
  stops,
  setStops,
  min,
  max,
  disabled,
}) {
  const inputRefs = React.useRef([]);
  const [focused, setFocused] = React.useState(null);

  const canAddStop = max === null || stops.length < max;
  const canDeleteStop = min === null || stops.length > min;

  React.useEffect(() => {
    if (focused !== null) {
      inputRefs.current[focused].focus();
    }
  }, [focused, stops.length]);

  const setNthStop = (n) => {
    return (stop) => {
      setStops([...stops.slice(0, n), stop, ...stops.slice(n + 1)]);
    };
  };

  const addNthStop = (n) => {
    setStops([...stops.slice(0, n), "", ...stops.slice(n)]);
    setFocused(n);
  };

  const addStop = () => {
    addNthStop(Math.max(stops.length - 1, 1));
  };

  const deleteNthStop = (n) => {
    if (!canDeleteStop) {
      return;
    }
    setStops([...stops.slice(0, n), ...stops.slice(n + 1)]);
    setFocused(Math.max(n - 1, 0));
  };

  const handleBackspace = (n) => {
    return (e) => {
      if (e.nativeEvent.key == "Backspace" && n != 0 && stops[n] === "") {
        deleteNthStop(n);
      }
    };
  };

  return (
    <ScrollView keyboardShouldPersistTaps="always">
      {stops.map((stop, n) => (
        <TextInput
          key={n}
          ref={(el) => (inputRefs.current[n] = el)}
          value={stop}
          right={
            <TextInput.Icon
              name="close"
              color="lightgray"
              onPress={() => deleteNthStop(n)}
              disabled={disabled || !canDeleteStop}
            />
          }
          disabled={disabled}
          onChangeText={setNthStop(n)}
          onSubmitEditing={() => addNthStop(n + 1)}
          onKeyPress={handleBackspace(n)}
          blurOnSubmit={false}
          returnKeyType="next"
          placeholder="Wpisz nazwę przystanku..."
          placeholderTextColor="lightgray"
          underlineColor="lightgray"
          style={{ backgroundColor: "white", height: 50 }}
        />
      ))}
      {canAddStop && (
        <Button icon="plus" color="gray" disabled={disabled} onPress={addStop}>
          Dodaj
        </Button>
      )}
    </ScrollView>
  );
}
