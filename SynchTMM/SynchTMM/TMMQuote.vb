
Imports System.IO
Imports System.Text
Class TMMQuote : Inherits TMMObject
    Public Sub New(ByVal objectType As String)
        MyBase.New(objectType)
    End Sub
    Public Overloads Sub GetTMMObject(userName As String, userPassword As String, params As Object())

        Dim Cookies As System.Net.CookieContainer
        Cookies = New System.Net.CookieContainer()

        Dim CRMDBWS As TMMWebService.CRMDBWebService
        Dim ticket As String

        CRMDBWS = New TMMWebService.CRMDBWebService

        'Enable Cookies since web service uses session information
        CRMDBWS.CookieContainer = Cookies
        'Authenticate
        ticket = CRMDBWS.authenticate(userName, userPassword)
        If (ticket.ToString().Trim() = "") Then
            Console.WriteLine("Ticket :" & ticket.ToString())
            Throw (New InvalidTicketException("Invalid User Name or User Password"))
        Else
            Console.WriteLine("Ticket :" & ticket.ToString())
        End If

        Dim strXMLData As String
        Dim strbldrData As New StringBuilder
        Dim objParams As Object
        strbldrData.Append("<?xml version=""1.0""?>" & vbCrLf & "<Data>" & vbCrLf)

        If ((params.Last = "Null" Or params.Last = "Yes")) Then
            objParams = {params.First, "Yes"}
            cntRow = CRMDBWS.queryRows(ticket, SPName, _objectType, objParams)
            Console.WriteLine("Total Row Count for Converted To Contracts = ""Yes"":" & cntRow.ToString())
            If cntRow > 0 Then
                For i As Integer = 0 To cntRow \ 1000 'Integer only part of division
                    'Fetch max 1000 rows at a time
                    strXMLData = CRMDBWS.fetchRowsByCount(ticket, i * 1000, 1000)
                    strbldrData.Append(strXMLData.Replace("<?xml version=""1.0""?>", "").Replace("<Rows>", "").Replace("</Rows>", "") & vbCrLf)
                Next
            End If
        End If
        If ((params.Last = "Null" Or params.Last = "No")) Then
            objParams = {params.First, "No"}
            cntRow = CRMDBWS.queryRows(ticket, SPName, _objectType, objParams)
            Console.WriteLine("Total Row Count for Converted To Contracts = ""No"":" & cntRow.ToString())
            If cntRow > 0 Then
                For i As Integer = 0 To cntRow \ 1000 'Integer only part of division
                    'Fetch max 1000 rows at a time
                    strXMLData = CRMDBWS.fetchRowsByCount(ticket, i * 1000, 1000)
                    strbldrData.Append(strXMLData.Replace("<?xml version=""1.0""?>", "").Replace("<Rows>", "").Replace("</Rows>", "") & vbCrLf)
                Next
            End If
        End If
        strbldrData.Append("</Data>" & vbCrLf)

        docXML = strbldrData.ToString 'Check strViewCust String for output or save to file
    End Sub
End Class