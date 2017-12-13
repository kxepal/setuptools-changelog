Fix zero division issue.

This happens when we pass second parameter as zero. Now in this case we
return default value instead of raising division exception.
