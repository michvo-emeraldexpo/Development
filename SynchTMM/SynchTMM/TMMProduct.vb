
Imports System.IO
Imports System.Text
Class TMMProduct : Inherits TMMObject
    Public Sub New(ByVal objectType As String)
        MyBase.New(objectType)
    End Sub
    Public Overloads Sub GetTMMObject(userName As String, userPassword As String, params As Object())
        MyBase.GetTMMOBject(userName, userPassword, params)
    End Sub
End Class