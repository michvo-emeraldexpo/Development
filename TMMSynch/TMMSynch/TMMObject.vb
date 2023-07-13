
Imports System.IO
Imports System.Text

Class TMMObject
    Public Property docXML As String
    Public cntRow As Integer
    Public Property SPName As String
    Private _objectType As String

    Public Sub New(objectType As String)
        _objectType = objectType
    End Sub
    Public Class InvalidTicketException : Inherits ApplicationException
        Public Sub New(ByVal text As String)
            MyBase.New(text)
        End Sub
    End Class
    Public Sub GetTMMOBject(userName As String, userPassword As String, params As Object())

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


        'Query Customers utilizing generic web methods queryRows and New fetchRowsByCount
        'Params- 4: [Customer Date Added From],[Customer Date Added To],[Customer Date Last Modified From],[Customer Date Last Modified To]
        'Dim params As Object() = {"1/1/2020", "12/31/2020", "12/1/2020", "12/31/2020"}

        cntRow = CRMDBWS.queryRows(ticket, SPName, _objectType, params)
        Console.WriteLine("Total Row Count :" & cntRow.ToString())
        Dim strXMLData As String
        Dim strbldrData As New StringBuilder
        strbldrData.Append("<?xml version=""1.0""?>" & vbCrLf & "<Data>" & vbCrLf)
        If cntRow > 0 Then
            For i As Integer = 0 To cntRow \ 1000 'Integer only part of division
                'Fetch max 1000 rows at a time
                strXMLData = CRMDBWS.fetchRowsByCount(ticket, i * 1000, 1000)
                strbldrData.Append(strXMLData.Replace("<?xml version=""1.0""?>", "").Replace("<Rows>", "").Replace("</Rows>", "") & vbCrLf)
            Next
        End If
        strbldrData.Append("</Data>" & vbCrLf)

        docXML = strbldrData.ToString 'Check strViewCust String for output or save to file
    End Sub
    Public Sub GetTMMOBject(userName As String, userPassword As String, params As Object(), dataMergeInd As Boolean)

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


        'Query Customers utilizing generic web methods queryRows and New fetchRowsByCount
        'Params- 4: [Customer Date Added From],[Customer Date Added To],[Customer Date Last Modified From],[Customer Date Last Modified To]
        'Dim params As Object() = {"1/1/2020", "12/31/2020", "12/1/2020", "12/31/2020"}
        Dim strXMLData As String
        Dim strbldrData As New StringBuilder
        Dim objParams As Object
        strbldrData.Append("<?xml version=""1.0""?>" & vbCrLf & "<Data>" & vbCrLf)

        If (dataMergeInd = True And (params.Last = "Null" Or params.Last = "Yes")) Then
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
        If (dataMergeInd = True And (params.Last = "Null" Or params.Last = "No")) Then
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
    Public Sub GenerateCSVFile(filePath As String, ObjectType As String, ColumnSeperator As String)
        Dim heading As New StringBuilder
        Dim titleLine As Boolean = True
        Dim doc As XDocument = XDocument.Parse(docXML)
        Dim theOutput As New StringBuilder
        For Each node As XElement In doc.Descendants(_objectType)
            ' Console.WriteLine(node)
            For Each innerNode As XElement In node.Elements()
                If IsNumeric(innerNode.Value) Then
                    theOutput.AppendFormat("@~^{0}@~^" + ColumnSeperator, innerNode.Value)
                Else
                    theOutput.AppendFormat("@~^{0}@~^" + ColumnSeperator, innerNode.Value)
                End If
                If titleLine Then
                    heading.AppendFormat("{0}" + ColumnSeperator, innerNode.Name.ToString())
                End If
                'Console.WriteLine(innerNode.Name.ToString())
            Next
            If titleLine Then
                heading.Remove(heading.Length - Len(ColumnSeperator), Len(ColumnSeperator))
                heading.AppendLine()
                titleLine = False
            End If
            ' Remove trailing comma
            theOutput.Remove(theOutput.Length - Len(ColumnSeperator), Len(ColumnSeperator))
            'Console.WriteLine(theOutput)
            theOutput.AppendLine()
        Next
        theOutput.Insert(0, heading.ToString())
        If cntRow > 0 Then
            File.WriteAllText(filePath, theOutput.ToString())
        End If
    End Sub
    Public Sub GenerateCSVFileProduct(filePath As String, ObjectType As String)
        Dim heading As New StringBuilder
        Dim titleLine As Boolean = True
        Dim doc As XDocument = XDocument.Parse(docXML)
        Dim theOutput As New StringBuilder
        For Each node As XElement In doc.Descendants(_objectType)
            ' Console.WriteLine(node)
            For Each innerNode As XElement In node.Elements()
                If IsNumeric(innerNode.Value) Then
                    theOutput.AppendFormat("@~^{0}@~^,", innerNode.Value)
                Else
                    theOutput.AppendFormat("@~^{0}@~^,", innerNode.Value)
                End If
                If titleLine Then
                    heading.AppendFormat("{0},", innerNode.Name.ToString())
                End If
                'Console.WriteLine(innerNode.Name.ToString())
            Next
            If titleLine Then
                heading.Remove(heading.Length - 1, 1)
                heading.AppendLine()
                titleLine = False
            End If
            ' Remove trailing comma
            theOutput.Remove(theOutput.Length - 1, 1)
            'Console.WriteLine(theOutput)
            theOutput.AppendLine()
        Next
        theOutput.Insert(0, heading.ToString())
        If cntRow > 0 Then
            File.WriteAllText(filePath, theOutput.ToString())

            Dim FileContent As String = File.ReadAllText(filePath)
            FileContent = FileContent.Replace(Chr(13), "")
            FileContent = FileContent.Replace(Chr(10), Chr(13) + Chr(10))
            File.WriteAllText(filePath, FileContent)
        End If
    End Sub
End Class


