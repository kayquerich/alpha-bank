from django.shortcuts import render

def test_view(request):

    context = {
        'message': 'This is a test view',
        'user' : 'Kayque',
        'range': range(0,10)
    }

    return render(request, 'test.html', context)