USE [CafeDB]
GO

/****** Object:  Trigger [dbo].[trg_UpdateTotalPrice]    Script Date: 4/3/2026 12:17:09 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE TRIGGER [dbo].[trg_UpdateTotalPrice]
ON [dbo].[ORDER_ITEM]
AFTER INSERT
AS
BEGIN
    UPDATE [ORDER]
    SET Total_Price = (
        SELECT SUM(Subtotal)
        FROM ORDER_ITEM
        WHERE Order_ID = (SELECT Order_ID FROM inserted)
    )
    WHERE Order_ID = (SELECT Order_ID FROM inserted)
END;
GO

ALTER TABLE [dbo].[ORDER_ITEM] ENABLE TRIGGER [trg_UpdateTotalPrice]
GO

