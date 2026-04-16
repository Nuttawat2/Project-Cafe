USE [CafeDB]
GO

/****** Object:  Trigger [dbo].[trg_ReduceStock]    Script Date: 4/17/2026 12:58:16 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE TRIGGER [dbo].[trg_ReduceStock]
ON [dbo].[ORDER_ITEM]
AFTER INSERT
AS
BEGIN
    UPDATE INGREDIENT
    SET Current_Stock = Current_Stock - (R.Quantity_Used * I.Quantity)
    FROM INGREDIENT ING
    JOIN RECIPE R ON ING.Ingredient_ID = R.Ingredient_ID
    JOIN inserted I ON R.Menu_ID = I.Menu_ID
END;
GO

ALTER TABLE [dbo].[ORDER_ITEM] ENABLE TRIGGER [trg_ReduceStock]
GO

