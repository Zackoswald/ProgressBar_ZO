# ProgressBar_ZO
Simple Progress Bar initialize immediately.

Usage:

```Python
toggle when iterated:
[ i for i in ProgressBar(range(20))]
or
for i in ProgressBar(range(10)):
	time.sleep(1)
```

Parameter Configuration:

```
ProgressBar(data: Iterable, body: str = "", head: str = "", scale: int = 1, track: bool = True, text: str = "")
data: iterable item list 
body: progress bar body symbol default: =
head: progress bar head symbol default: >
scale: enlarge or shink progress bar size with certificate rate (unfinished)
track: whether enable progress bar or not 
text: display text with iterating elements
	etc: for i in ProgressBar(range(10), text="processing no.$1 ")
		 for k, v in ProgressBar({'a': 1, 'b': 2}.items(), text="processing $1, value is $2")
		 it will display stack like text after the bar displayed.
```

