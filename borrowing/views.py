from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from books.models import Book
from .models import Loan


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    existing_loan = Loan.objects.filter(
        member=request.user,
        book=book,
        status='borrowed'
    ).exists()

    if existing_loan:
        messages.error(request, "You already borrowed this book.")
        return redirect('book_list')

    if book.available_copies <= 0:
        messages.error(request, "No available copies of this book.")
        return redirect('book_list')

    Loan.objects.create(
        member=request.user,
        book=book
    )

    book.available_copies -= 1
    book.save()

    messages.success(
        request,
        f"You borrowed '{book.title}' successfully."
    )

    return redirect('book_list')


@login_required
def my_loans(request):
    loans = Loan.objects.filter(
        member=request.user
    ).order_by('-borrow_date')

    return render(request, 'borrowing/my_loans.html', {
        'loans': loans
    })


@login_required
def return_book(request, loan_id):
    loan = get_object_or_404(
        Loan,
        id=loan_id,
        member=request.user,
        status='borrowed'
    )

    loan.status = 'returned'
    loan.return_date = timezone.now()
    loan.save()

    loan.book.available_copies += 1
    loan.book.save()

    messages.success(
        request,
        f"You returned '{loan.book.title}' successfully."
    )

    return redirect('my_loans')