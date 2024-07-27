# pytz-timezones
The IANA timezone database (while we are all grateful for it) is a convoluted mess.
There is little hope of implementing it entirely correctly in Hoon. At present it has resisted all attempts at simplification and legibility.
Therefore we will defer to prior art to ensure robustness and correctness and to drastically reduce the surface area for timezone bugs.

`pytz-timezones.py` is a script which uses the `pytz` library to extract from each official IANA timezone the datetime in UTC of a transition to a new offset,
the offset to which we are transitioning, and the name of the relevant rule (e.g. EST vs EDT or AEST vs AEDT).

With this radically simplified and reliable dataset (roughly 2.9MB), it is trivial to build functions in Hoon which convert a `@da` to or from a timezone by simply referring to this timezone data stored in a `+mop`.

- To go from UTC to a timezone: Use the mop to get the transition which immediately precedes your given datetime. (NOTE: This can be null if the datetime is out of bounds.)
- To go from a timezone to UTC: Generate a set of candidates by trying to offset the time using all possible offsets from the timezone. Reduce this to the set of datetimes which could have been validly generated by their corresponding most recent transition. (NOTE: This can be null if the datetime is out of bounds. It can also produce two values if the UTC datetime occurs in an hour which is "repeated" when a transition shifts the clock backwards.)

`/lib/pytz.hoon` contains a dedicated and standalone library which imports the timezones as raw data and provides an interface for converting between timezones.
