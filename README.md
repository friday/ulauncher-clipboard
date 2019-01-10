# ulauncher-clipboard

[Ulauncher](https://ulauncher.io) extension for managing your clipboard

<img src="screenshot.png" width="500">

## Usage

Open Ulauncher and type the keyword `c` followed by a space. This will search your clipboard history. Activate an entry (for example by pressing enter or clicking on it). This will copy it your actual clipboard. Now you can paste it elsewhere.

From Ulauncher's preferences you can change the keyword and the clipboard manager to use, number of results to be shown.

You can also add a *copy hook*. A command to run after copying a clipboard entry. This is mostly a way to support pasting directly, without adding or supporting any such code. Pasting directly isn't possible to achieve safely, but X11 users can use xdotool to trigger the key combinations "ctrl+v" or "shift+insert". This will not work in all applications, and may even have unwanted side effects, so beware!

```sh
xdotool key ctrl+v
```

If you want to use [GPaste](https://github.com/Keruspe/GPaste/) or [CopyQ](https://github.com/hluk/CopyQ), you have to install them. If you haven't. [Clipster](https://github.com/mrichar1/clipster) will be downloaded automatically.

## License

The code is licensed as MIT.

The icon is part of [Paper Icons](http://snwh.org/paper/icons) by [Sam Hewitt](http://samuelhewitt.com/), and is licensed under [CC-SA-4.0](http://creativecommons.org/licenses/by-sa/4.0/)
