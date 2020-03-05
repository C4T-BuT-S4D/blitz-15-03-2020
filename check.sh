#!/bin/bash

find . -name 'checker.py' | while read -r line; do
  echo "Processing checker '$line'"
  for i in {1..10}; do
    echo "Running check $i"
    "$line" check 127.0.0.1
    A=$?
    if [ $A != 101 ]; then
      echo "CHECK failed! Got code $A"
      exit 1
    else
      echo "CHECK passed!"
      true
    fi

    OUT=$("$line" put 127.0.0.1 123 AAAAAAAACAAAAAAAAAAAAABAAAAAAAA= 1)
    A=$?
    if [ $A != 101 ]; then
      echo "PUT failed! Got code $A"
      exit 1
    else
      echo "PUT passed!"
      true
    fi

    "$line" get 127.0.0.1 "$OUT" AAAAAAAACAAAAAAAAAAAAABAAAAAAAA= 1
    A=$?
    if [ $A != 101 ]; then
      echo "GET failed! Got code $A"
      exit 1
    else
      echo "GET passed!"
      true
    fi

    echo "Done check $i"
  done
done
