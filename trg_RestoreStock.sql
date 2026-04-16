USE [CafeDB]
GO

/****** Object:  Trigger [dbo].[trg_RestoreStock]    Script Date: 4/17/2026 12:58:37 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE TRIGGER [dbo].[trg_RestoreStock]
ON [dbo].[ORDER_ITEM]
AFTER DELETE
AS
BEGIN
    UPDATE INGREDIENT
    SET Current_Stock = Current_Stock + (R.Quantity_Used * d.Quantity)
    FROM INGREDIENT ING
    JOIN RECIPE R ON ING.Ingredient_ID = R.Ingredient_ID
    JOIN deleted d ON R.Menu_ID = d.Menu_ID
END;
GO

ALTER TABLE [dbo].[ORDER_ITEM] ENABLE TRIGGER [trg_RestoreStock]
GO

