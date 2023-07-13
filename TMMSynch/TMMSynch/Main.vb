
Imports System.IO
'Imports System.Web.Services.Protocols
Imports System.Text
Imports System.Environment
Module main
    Function Main() As Integer
        Dim ToDate As String = ""
        Dim FromDate As String = ""
        Dim UserName As String = ""
        Dim UserPassword As String = ""
        Dim FullFilePath As String = ""
        Dim ObjectType As String = ""
        Dim IssueYear As String = Year(Now).ToString()
        Dim ConvertedToContracts As String = "Null"
        Dim ExceptionGenerated As Boolean
        Dim Params As Object()
        Dim args() As String = System.Environment.GetCommandLineArgs()
        For i As Integer = 0 To args.Length - 1
            If (args(i) = "-TMMUserName") Then
                'parse the name value pair
                UserName = args(i + 1).Trim()
            End If
            If (args(i) = "-TMMUserPassword") Then
                'parse the name value pair
                UserPassword = args(i + 1).Trim()
            End If
            If (args(i) = "-TMMFromDate") Then
                'parse the name value pair
                FromDate = args(i + 1).Trim()
            End If
            If (args(i) = "-TMMToDate") Then
                'parse the name value pair
                ToDate = args(i + 1).Trim()
            End If
            If (args(i) = "-TMMIssueYear") Then
                'parse the name value pair
                IssueYear = args(i + 1).Trim()
            End If
            If (args(i) = "-TMMConvertedToContracts") Then
                'parse the name value pair
                ConvertedToContracts = args(i + 1).Trim()
            End If
            If (args(i) = "-TMMFullFilePath") Then
                'parse the name value pair
                FullFilePath = args(i + 1).Trim()
            End If
            If (args(i) = "-TMMObjectType") Then
                'parse the name value pair
                ObjectType = args(i + 1).Trim()
            End If
        Next

        'Setting values locally for Unit Testing

        'ToDate = "01/20/2021"
        'FromDate = "01/01/2010"
        UserName = "Euser"
        UserPassword = "Test11Pwd"
        FullFilePath = "D:\Import\TMM\TMMQuote.txt"
        ObjectType = "Quote"

        Console.WriteLine("User Name: " & UserName)
        Console.WriteLine("User Password : " & UserPassword)
        If FromDate <> "" Then
            Console.WriteLine("From Date: " & FromDate)
        End If
        If ToDate <> "" Then
            Console.WriteLine("To Date: " & ToDate)
        End If
        Console.WriteLine("Full Path: " & FullFilePath)
        Console.WriteLine("Object Type : " & ObjectType)
        Try
            Select Case ObjectType
                Case "Customer"
                    Console.WriteLine("Stored Procedure Name: spCustomEmeraldCustomerSearchCDH_199")
                    If FromDate = "" Then
                        Throw New System.Exception("From Date is Blank")
                    End If
                    If ToDate = "" Then
                        Throw New System.Exception("To Date is Blank")
                    End If
                    Params = {FromDate, ToDate, FromDate, ToDate}
                    Dim TMMObject As New TMMObject(ObjectType)
                    TMMObject.SPName = "spCustomEmeraldCustomerSearchCDH_199"
                    TMMObject.GetTMMOBject(UserName, UserPassword, Params)
                    FileValidation(FullFilePath, ObjectType)
                    TMMObject.GenerateCSVFile(FullFilePath, ObjectType, ",")
                Case "Product"
                    Console.WriteLine("Stored Procedure Name: spCustomEmeraldProductSearchCDH_200")
                    Params = {}
                    Dim TMMObject As New TMMObject(ObjectType)
                    TMMObject.SPName = "spCustomEmeraldProductSearchCDH_200"
                    TMMObject.GetTMMOBject(UserName, UserPassword, Params)
                    FileValidation(FullFilePath, ObjectType)
                    TMMObject.GenerateCSVFileProduct(FullFilePath, ObjectType)
                Case "Quote"
                    Console.WriteLine("Stored Procedure Name: spCustomEmeraldForecastingReport_198")
                    Params = {IssueYear, ConvertedToContracts}
                    Dim TMMObject As New TMMObject(ObjectType)
                    TMMObject.SPName = "spCustomEmeraldForecastingReport_198"
                    TMMObject.GetTMMOBject(UserName, UserPassword, Params, True)
                    FileValidation(FullFilePath, ObjectType)
                    TMMObject.GenerateCSVFile(FullFilePath, ObjectType, "*|*")
                    'Case "Contact"
                    '    Console.WriteLine("No Contact")
                Case Else
                    Throw (New InvalidOjectTypeException("Invalid Object Type"))
            End Select

            ExceptionGenerated = False
            'System.Threading.Thread.Sleep(5000)
            Return 0
        Catch ex As System.IO.IOException
            ' Show the exception.
            Console.WriteLine("IOException: " & ex.Message)
            Console.WriteLine("Stack Trace: " & vbCrLf & ex.StackTrace)
            ExceptionGenerated = True
            Return 1
        Catch ex As NullReferenceException
            ' Show the exception.
            Console.WriteLine("NullReferenceException: " & ex.Message)
            Console.WriteLine("Stack Trace: " & vbCrLf & ex.StackTrace)
            ExceptionGenerated = True
            Return 1
        Catch ex As System.OutOfMemoryException
            ' Show the exception.
            Console.WriteLine("OutOfMemoryException: " & ex.Message)
            Console.WriteLine("Stack Trace: " & vbCrLf & ex.StackTrace)
            ExceptionGenerated = True
            Return 1
        Catch ex As TMMObject.InvalidTicketException
            ' Show the exception.
            Console.WriteLine("InvalidTicketException: " & ex.Message)
            Console.WriteLine("Stack Trace: " & vbCrLf & ex.StackTrace)
            ExceptionGenerated = True
            Return 1
        Catch ex As FilePathBlankException
            ' Show the exception.
            Console.WriteLine("FilePathBlankException: " & ex.Message)
            Console.WriteLine("Stack Trace: " & vbCrLf & ex.StackTrace)
            ExceptionGenerated = True
            Return 1
        Catch ex As FileNameOrFileExtesnionInvalidException
            ' Show the exception.
            Console.WriteLine("FileNameOrFileExtesnionInvalidException: " & ex.Message)
            Console.WriteLine("Stack Trace: " & vbCrLf & ex.StackTrace)
            ExceptionGenerated = True
            Return 1
        Catch ex As InvalidOjectTypeException
            ' Show the exception.
            Console.WriteLine("InvalidOjectTypeException: " & ex.Message)
            Console.WriteLine("Stack Trace: " & vbCrLf & ex.StackTrace)
            ExceptionGenerated = True
            Return 1
        Catch ex As Exception
            ' Show the exception.
            Console.WriteLine("OtherException: " & ex.Message)
            Console.WriteLine("Stack Trace: " & vbCrLf & ex.StackTrace)
            ExceptionGenerated = True
            Return 1
        Finally
            If ExceptionGenerated = False Then
                Console.WriteLine("TMM CSV File Generation Completed Successfully")
            Else
                Console.WriteLine("TMM CSV File Generation Failed")
            End If
        End Try
    End Function
    Public Class InvalidOjectTypeException : Inherits ApplicationException
        Public Sub New(ByVal text As String)
            MyBase.New(text)
        End Sub
    End Class
    Public Class FilePathBlankException : Inherits ApplicationException
        Public Sub New(ByVal text As String)
            MyBase.New(text)
        End Sub
    End Class
    Public Class FileNameOrFileExtesnionInvalidException : Inherits ApplicationException
        Public Sub New(ByVal text As String)
            MyBase.New(text)
        End Sub
    End Class
    Public Sub FileValidation(filepath As String, ObjectType As String)
        If (filepath.ToString().Trim() = "") Then
            Throw (New FilePathBlankException("File Path is Blank"))
        End If
        If ((Path.GetFileNameWithoutExtension(filepath).ToString().Trim() = "TMM" & ObjectType.ToString().Trim()) Or (Path.GetExtension(filepath).ToString().Trim() = ".csv") Or (Path.GetExtension(filepath).ToString().Trim() = ".txt")) Then
            Console.WriteLine("File Name Or File Extension is Valid")
        Else
            Throw (New FileNameOrFileExtesnionInvalidException("File Name Or File Extension is Invalid"))
        End If
    End Sub
End Module
