DECLARE @MinTenure INT = 2;
DECLARE @MaxBalance DECIMAL = 70000;
DECLARE @MaxProducts INT = 3
SELECT
	A.[CustomerId],
	A.[Tenure],
	A.[Balance],
	A.[NumProducts]

FROM [dbo].[account] A
JOIN [dbo].[demographic] D ON D.[CustomerId] = A.[CustomerId]
WHERE	
	[Tenure] > @MinTenure
	AND [Balance] < @MaxBalance
	AND [NumProducts] < @MaxProducts

