Translit is a small application for transliterating and transforming text in
your clipboard.

It sits in your indicator space as an "λ" icon. Clicking that gives you a list
of options to transform the text currently in your clipboard. You can also
select "Options" to choose which transformations to show and which to hide. This
can help if you have a lot of plugins.

# Writing plugins #

Writing your own plugins is not very hard. Remember to put them in
`~/.local/share/translit/transforms/`.

The first line is the name of your plugin. You have two options: one way
conversion or two way conversion. The last one has `->` in the middle, the
former does not.

Example:

    Latin->Greek

The above will add two transformation options to the menu: from Latin to Greek,
and the reverse one, from Greek to Latin.

Each next line can start with `s`, `r` or `p`, optionally preceded by `<` or
`>`.

`r` means plain text replacement, `s` uses regular expressions and `p` is a
snippet of Python code.

`>` means that that line is only for the "nomal" transformation, while `<` means
that it is for "reverse" transformation only. Without one of either, it will be
done in both ways, in case it is a two way conversion.

What follows next is the separator character, which can be anything you want.
Usually, people pick `/` for things like that.

Examples:

    r/:-(/:-)/

The above will transform all frowny emoticons to happy ones (or the other way
around for reverse transformations).

    >s/([a-z])s/\1/

The above will transform any lower case letter followed by an `s` to just that
letter. For example, `"it shows success"` will be transformed to `"it show
succes"`.

Note this one is one-way. Regexes usually don't make much sense the other way
around.

If you'd like to do some regular expression just when reversing, do:

    <s/leet/([l1]|\|_)33[t7]/

This one, when used in reverse, will change things like `"l33t"`, `"1337"` and
`"|_33t"` to `"leet"`. Note that the position of regex and target are reversed.

    p/_.upper()/

Python snippets work a bit differently. They don't have a target part. They
operate on the whole text. They act like `text = (lambda _: ...)(text)`

So the example above works like this:

    text = (lambda _: _.upper())(text)

Or:

    text = text.upper()

What I called "lines" earlier are actually *rules*, that can span multiple
lines, because they are delimited by the seperator character.

Another way of writing the emoticon example:

    r
    :-(
    :-)

Here we use the new line character as separator. Note that if you do that, it is
important not to forget the very last new line.

If this explanation didn't make sense to you, or you'd like to learn more,
please [contact me](http://robinwell.net/about).
